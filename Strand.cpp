#include "Strand.h"
using namespace llvm;

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
        for (Instruction &I: B) {
          // Inst* i = new Inst();
          // Value* op = dyn_cast<Value>(I.getOperandList());
          // uses.insert(I , op);
          errs() << "Instruction:" << I << "\n";
          for (Use &U : I.operands()) {
            Value *v = U.get();
            // use.insert(*v);
            errs() << "Value:" << *v << "\n";

            if(isa<User>(v)){
              errs() << "Def:" << *(dyn_cast<User>(v)) << "\n";
              User* u = dyn_cast<User>(v);

              if(isa<Instruction>(u)){
                errs() << "Def In:" << *(dyn_cast<Instruction>(u)) << "\n";
              }
              else{
                errs() << "Can't cast Instruction\n";
              }
            }
            else{
              errs() << "Can't cast User\n";
            }

            errs() << "Operand type:" << *(v->getType()) << '\n';
            // errs() << "Operand context:" << dyn_cast<raw_ostream>(v->getContext()) << '\n';
            errs() << "Operand Name:" << v->getName() << '\n';
            // errs() << "Operand ValueName:" << *(v->getValueName()) << '\n';
          }
          errs().write_escaped(I.getOpcodeName()) << '\n';
        }
        errs() << "------------------------\n";
      }
      return false;
    }
  };
}
char Strand::ID = 0;
static RegisterPass<Strand> X("Strand", "Strand Pass",
                             false /* Only looks at CFG */,
                             false /* Analysis Pass */);
