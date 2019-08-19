#include "Strand.h"
using namespace llvm;

typedef std::vector<llvm::Instruction *> strand

void AddInst(strand st, Instruction Ins, strand unuse){
  for (Use &U : Ins.operands()) {
    Value *v = U.get();
    errs() << "Value:" << *v << "\n";

    if(isa<User>(v)){
      errs() << "Def:" << *(dyn_cast<User>(v)) << "\n";
      User* u = dyn_cast<User>(v);

      if(isa<Instruction>(u)){
        errs() << "Def In:" << *(dyn_cast<Instruction>(u)) << "\n";
        Instruction* In = dyn_cast<Instruction>(u);
        unuse.pop(In);
        st.insert(In);
        AddInst(st, In, unuse);
      }
      else{
        errs() << "Can't cast Instruction\n";
      }
    }
    else{
      errs() << "Can't cast User\n";
    }
  }
}

namespace {
  struct Strand : public FunctionPass {
    static char ID;
    Strand() : FunctionPass(ID) {}
    virtual bool runOnFunction(Function& F) {
      errs() << F.getFunction() << "\n";
      errs() << "=============================\n";
      // std::hash_map<llvm::Instruction *,std::set<llvm::Value *>> uses , defs;
      // std::set<llvm::Value> use;
      for (BasicBlock &B : F) {
        std::vector<llvm::Instruction *> unuse;
        std::vector<strand> strands;
        for (Instruction &I: B) {
          // Inst* i = new Inst();
          // Value* op = dyn_cast<Value>(I.getOperandList());
          // uses.insert(I , op);
          errs() << "Instruction:" << I << "\n";
          unuse.insert(&I);
        }
        while(unuse!= empty){
          Instruction* I = unuse.pop();
          strand st;
          AddInst(st, I, unuse);
          strands.insert(st);
        }

//             errs() << "Operand type:" << *(v->getType()) << '\n';
//             errs() << "Operand Name:" << v->getName() << '\n';
//           errs().write_escaped(I.getOpcodeName()) << '\n';
        }
        for(strand s : strands){
          errs() << "--------------Strands-------------\n";
          for(Instrction* I : s){
            errs() << *I <<"\n";
          }
          errs() << "------------------------\n";
        }
      }
      return false;
    }
  };
}
char Strand::ID = 0;
static RegisterPass<Strand> X("Strand", "Strand Pass",
                             false /* Only looks at CFG */,
                             false /* Analysis Pass */);
